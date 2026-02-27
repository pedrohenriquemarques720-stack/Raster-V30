class SecurityManager {
    async validateRequest(request) {
        // 1. Rate limiting por IP
        await this.rateLimiter.check(request.ip);
        
        // 2. Verificar token de sessão
        const sessionValid = await this.validateSession(request.token);
        
        // 3. Análise de comportamento
        const behaviorScore = await this.analyzeBehavior(request);
        
        if (behaviorScore < 0.5) {
            await this.triggerAdditionalAuth(request);
        }
        
        // 4. Verificar geolocalização suspeita
        const locationRisk = await this.checkLocationRisk(request.ip);
        
        if (locationRisk > 0.8) {
            throw new Error('HIGH_RISK_LOCATION');
        }
        
        return {
            allowed: true,
            riskScore: behaviorScore,
            requires2FA: behaviorScore < 0.3
        };
    }

    async analyzeBehavior(request) {
        const userPatterns = await this.database.behavior.findOne({
            userId: request.userId
        });
        
        // Analisar padrões incomuns
        const anomalies = [];
        
        if (request.deviceCount > userPatterns.averageDevices * 2) {
            anomalies.push('UNUSUAL_DEVICE_COUNT');
        }
        
        if (request.updateFrequency > userPatterns.averageFrequency * 3) {
            anomalies.push('UNUSUAL_UPDATE_FREQUENCY');
        }
        
        return anomalies.length === 0 ? 1.0 : 0.3;
    }
}