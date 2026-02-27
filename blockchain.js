class LicenseBlockchain {
    constructor() {
        this.contract = new web3.eth.Contract(LICENSE_CONTRACT_ABI);
    }

    async registerLicense(licenseData) {
        // Registrar licença na blockchain
        const tx = await this.contract.methods.registerLicense(
            licenseData.key,
            licenseData.plan,
            licenseData.expirationDate
        ).send({ from: process.env.ADMIN_WALLET });
        
        return tx.transactionHash;
    }

    async verifyLicense(licenseKey) {
        // Verificar na blockchain
        const record = await this.contract.methods.getLicense(licenseKey).call();
        
        return {
            valid: record.isValid,
            plan: record.plan,
            expirationDate: new Date(record.expirationDate * 1000),
            revoked: record.revoked,
            transactionHash: record.txHash
        };
    }
}