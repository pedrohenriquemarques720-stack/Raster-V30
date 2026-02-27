class LicenseManager {
    constructor() {
        this.encryptionKey = process.env.LICENSE_KEY_SECRET;
        this.blockchain = new LicenseBlockchain();
    }

    async validateLicense(licenseKey, deviceId) {
        // 1. Verificar formato
        if (!this.isValidFormat(licenseKey)) {
            return { valid: false, reason: 'INVALID_FORMAT' };
        }

        // 2. Verificar no blockchain
        const blockchainRecord = await this.blockchain.verifyLicense(licenseKey);
        
        // 3. Verificar se não está revogada
        if (blockchainRecord.revoked) {
            return { valid: false, reason: 'LICENSE_REVOKED' };
        }

        // 4. Verificar validade temporal
        const now = new Date();
        if (now > blockchainRecord.expirationDate) {
            return { valid: false, reason: 'LICENSE_EXPIRED' };
        }

        // 5. Verificar limite de dispositivos
        const devicesCount = await this.getDevicesCount(licenseKey);
        const plan = subscriptionPlans[blockchainRecord.plan];
        
        if (devicesCount >= plan.limits.devicesAllowed && 
            plan.limits.devicesAllowed !== 'unlimited') {
            return { valid: false, reason: 'MAX_DEVICES_REACHED' };
        }

        // 6. Gerar token de sessão
        const sessionToken = this.generateSessionToken(licenseKey, deviceId);
        
        return {
            valid: true,
            plan: blockchainRecord.plan,
            features: plan.features,
            sessionToken: sessionToken,
            expiresAt: blockchainRecord.expirationDate
        };
    }

    generateSessionToken(licenseKey, deviceId) {
        const payload = {
            licenseKey: this.hash(licenseKey),
            deviceId: deviceId,
            timestamp: Date.now(),
            nonce: crypto.randomBytes(16).toString('hex')
        };
        
        return jwt.sign(payload, this.encryptionKey, { expiresIn: '24h' });
    }
}