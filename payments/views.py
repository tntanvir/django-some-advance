


import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


# ✅ 1. Create Stripe Checkout Session
class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            priceid = request.data.get("priceid")
            user = request.user

            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    "price": priceid,
                    "quantity": 1
                }],
                mode='subscription',
                success_url="http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:3000/cancel/",
                customer_email=user.email,  # associate session with the user's email
            )

            # Create Payment object linked to this session
            Payment.objects.create(
                user=user,
                stripe_session_id=checkout_session.id,
                amount=0,  # will update after webhook (Stripe doesn’t provide here)
                status='created'
            )

            print("Checkout Session created:", checkout_session.id)
            return Response({"checkout_url": checkout_session.url})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)



# ✅ 2. Handle Stripe Webhook
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        # Handle successful checkout session
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            try:
                # Retrieve full session details
                checkout_session = stripe.checkout.Session.retrieve(
                    session['id'],
                    expand=['line_items', 'payment_intent']
                )

                # Find Payment using session ID (reliable!)
                payment = Payment.objects.filter(stripe_session_id=checkout_session.id).first()
                if not payment:
                    print("No payment record found for session:", checkout_session.id)
                    return HttpResponse(status=404)

                # Update payment with Stripe details
                payment.amount = checkout_session.amount_total / 100
                payment.stripe_payment_intent = checkout_session.payment_intent
                payment.status = 'succeeded'
                payment.save()

                # Update user subscription
                user = payment.user
                user.is_subscribed = True

                print(payment)

                # Determine plan
                price_id_to_tier = {
                    'price_go_id': 'go',
                    'price_plus_id': 'plus',
                    'price_pro_id': 'pro',
                }

                if checkout_session.line_items.data:
                    price_id = checkout_session.line_items.data[0].price.id
                    user.subscribed_model = price_id_to_tier.get(price_id, 'go')

                user.save()
                print(f"✅ Payment success for {user.email}, plan: {user.subscribed_model}")

            except Exception as e:
                print("Error processing webhook:", e)
                return HttpResponse(status=500)

        return HttpResponse(status=200)
