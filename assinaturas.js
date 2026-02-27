class PaymentProcessor {
    constructor() {
        this.stripe = new Stripe(process.env.STRIPE_KEY);
        this.asaas = new Asaas(process.env.ASAAS_KEY); // Para Brasil
    }

    async createSubscription(userData, planId, paymentMethod) {
        // 1. Criar cliente no gateway
        const customer = await this.createCustomer(userData, paymentMethod);
        
        // 2. Criar assinatura
        const plan = subscriptionPlans[planId];
        const subscription = await this.stripe.subscriptions.create({
            customer: customer.id,
            items: [{ price: plan.stripePriceId }],
            payment_behavior: 'default_incomplete',
            expand: ['latest_invoice.payment_intent'],
            metadata: {
                userId: userData.id,
                planId: planId
            }
        });
        
        // 3. Gerar licença
        const licenseKey = await this.generateLicenseKey(userData.id, planId);
        
        // 4. Associar licença à assinatura
        await this.database.licenses.insertOne({
            licenseKey,
            userId: userData.id,
            subscriptionId: subscription.id,
            planId,
            status: 'active',
            createdAt: new Date(),
            expiresAt: this.calculateExpiration(plan.period)
        });
        
        return {
            subscriptionId: subscription.id,
            clientSecret: subscription.latest_invoice.payment_intent.client_secret,
            licenseKey
        };
    }

    async handleWebhook(event) {
        switch (event.type) {
            case 'invoice.payment_succeeded':
                await this.renewLicense(event.data.object);
                break;
                
            case 'invoice.payment_failed':
                await this.handlePaymentFailure(event.data.object);
                break;
                
            case 'customer.subscription.deleted':
                await this.revokeLicense(event.data.object);
                break;
        }
    }
}