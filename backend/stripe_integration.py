"""
Stripe Integration for Loop Factory AI
Handles payments, subscriptions, and customer management

Author: Manus AI
Date: October 17, 2025
"""

import os
import stripe
from typing import Dict, List, Optional
from datetime import datetime

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeIntegration:
    """Stripe integration for payment processing"""
    
    def __init__(self):
        self.api_key = stripe.api_key
        if not self.api_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable not set")
    
    # ========================================================================
    # PRODUCTS & PRICES
    # ========================================================================
    
    def create_product(self, name: str, description: str, metadata: Dict = None) -> stripe.Product:
        """Create a new product in Stripe"""
        return stripe.Product.create(
            name=name,
            description=description,
            metadata=metadata or {}
        )
    
    def create_price(self, product_id: str, amount_usd: float, interval: str = "month") -> stripe.Price:
        """Create a price for a product"""
        return stripe.Price.create(
            product=product_id,
            unit_amount=int(amount_usd * 100),  # Convert to cents
            currency="usd",
            recurring={"interval": interval} if interval else None
        )
    
    def sync_agent_to_stripe(self, agent_data: Dict) -> Dict:
        """Sync an agent to Stripe as a product"""
        # Create product
        product = self.create_product(
            name=agent_data["name"],
            description=agent_data.get("description", ""),
            metadata={
                "agent_id": agent_data["id"],
                "category": agent_data.get("category", ""),
                "company_id": agent_data.get("company_id", "")
            }
        )
        
        # Create price
        price = self.create_price(
            product_id=product.id,
            amount_usd=agent_data["price_usd"],
            interval="month" if agent_data.get("pricing_model") == "subscription" else None
        )
        
        return {
            "product_id": product.id,
            "price_id": price.id
        }
    
    # ========================================================================
    # CUSTOMERS
    # ========================================================================
    
    def create_customer(self, email: str, name: str = None, metadata: Dict = None) -> stripe.Customer:
        """Create a new customer in Stripe"""
        return stripe.Customer.create(
            email=email,
            name=name,
            metadata=metadata or {}
        )
    
    def get_customer(self, customer_id: str) -> stripe.Customer:
        """Get customer by ID"""
        return stripe.Customer.retrieve(customer_id)
    
    def update_customer(self, customer_id: str, **kwargs) -> stripe.Customer:
        """Update customer details"""
        return stripe.Customer.modify(customer_id, **kwargs)
    
    # ========================================================================
    # SUBSCRIPTIONS
    # ========================================================================
    
    def create_subscription(self, customer_id: str, price_id: str, metadata: Dict = None) -> stripe.Subscription:
        """Create a subscription for a customer"""
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            metadata=metadata or {},
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"]
        )
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> stripe.Subscription:
        """Cancel a subscription"""
        if at_period_end:
            return stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
        else:
            return stripe.Subscription.delete(subscription_id)
    
    def get_subscription(self, subscription_id: str) -> stripe.Subscription:
        """Get subscription by ID"""
        return stripe.Subscription.retrieve(subscription_id)
    
    def list_customer_subscriptions(self, customer_id: str) -> List[stripe.Subscription]:
        """List all subscriptions for a customer"""
        subscriptions = stripe.Subscription.list(customer=customer_id)
        return subscriptions.data
    
    # ========================================================================
    # ONE-TIME PAYMENTS
    # ========================================================================
    
    def create_payment_intent(self, amount_usd: float, customer_id: str, metadata: Dict = None) -> stripe.PaymentIntent:
        """Create a one-time payment intent"""
        return stripe.PaymentIntent.create(
            amount=int(amount_usd * 100),  # Convert to cents
            currency="usd",
            customer=customer_id,
            metadata=metadata or {}
        )
    
    def confirm_payment_intent(self, payment_intent_id: str, payment_method: str) -> stripe.PaymentIntent:
        """Confirm a payment intent"""
        return stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method=payment_method
        )
    
    # ========================================================================
    # CHECKOUT SESSIONS
    # ========================================================================
    
    def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: str = None,
        metadata: Dict = None
    ) -> stripe.checkout.Session:
        """Create a Stripe Checkout session"""
        params = {
            "mode": "subscription",
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": metadata or {}
        }
        
        if customer_email:
            params["customer_email"] = customer_email
        
        return stripe.checkout.Session.create(**params)
    
    # ========================================================================
    # WEBHOOKS
    # ========================================================================
    
    def construct_webhook_event(self, payload: bytes, sig_header: str, webhook_secret: str):
        """Construct and verify a webhook event"""
        return stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    
    def handle_webhook_event(self, event: stripe.Event) -> Dict:
        """Handle a webhook event"""
        event_type = event.type
        event_data = event.data.object
        
        handlers = {
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_payment_failed,
            "checkout.session.completed": self._handle_checkout_completed
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event_data)
        
        return {"status": "unhandled", "event_type": event_type}
    
    def _handle_subscription_created(self, subscription: stripe.Subscription) -> Dict:
        """Handle subscription created event"""
        return {
            "status": "subscription_created",
            "subscription_id": subscription.id,
            "customer_id": subscription.customer,
            "status": subscription.status
        }
    
    def _handle_subscription_updated(self, subscription: stripe.Subscription) -> Dict:
        """Handle subscription updated event"""
        return {
            "status": "subscription_updated",
            "subscription_id": subscription.id,
            "customer_id": subscription.customer,
            "status": subscription.status
        }
    
    def _handle_subscription_deleted(self, subscription: stripe.Subscription) -> Dict:
        """Handle subscription deleted event"""
        return {
            "status": "subscription_deleted",
            "subscription_id": subscription.id,
            "customer_id": subscription.customer
        }
    
    def _handle_invoice_paid(self, invoice: stripe.Invoice) -> Dict:
        """Handle invoice paid event"""
        return {
            "status": "invoice_paid",
            "invoice_id": invoice.id,
            "customer_id": invoice.customer,
            "amount_paid": invoice.amount_paid / 100  # Convert from cents
        }
    
    def _handle_invoice_payment_failed(self, invoice: stripe.Invoice) -> Dict:
        """Handle invoice payment failed event"""
        return {
            "status": "invoice_payment_failed",
            "invoice_id": invoice.id,
            "customer_id": invoice.customer,
            "amount_due": invoice.amount_due / 100
        }
    
    def _handle_checkout_completed(self, session: stripe.checkout.Session) -> Dict:
        """Handle checkout session completed event"""
        return {
            "status": "checkout_completed",
            "session_id": session.id,
            "customer_id": session.customer,
            "subscription_id": session.subscription
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_customer_portal_url(self, customer_id: str, return_url: str) -> str:
        """Create a customer portal session and return the URL"""
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        return session.url


# Example usage
if __name__ == "__main__":
    # Initialize
    stripe_integration = StripeIntegration()
    
    # Example: Create a product and price
    agent_data = {
        "id": "agent_123",
        "name": "KoiKeeper Water Quality Monitor",
        "description": "AI-powered water quality monitoring for koi ponds",
        "price_usd": 29.00,
        "pricing_model": "subscription",
        "category": "koi_management",
        "company_id": "koikeeper"
    }
    
    result = stripe_integration.sync_agent_to_stripe(agent_data)
    print(f"Created product: {result['product_id']}")
    print(f"Created price: {result['price_id']}")

