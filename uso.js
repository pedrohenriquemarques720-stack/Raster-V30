class AnalyticsSystem {
    async trackUpdate(deviceId, updateData) {
        const analytics = {
            deviceId,
            fromVersion: updateData.fromVersion,
            toVersion: updateData.toVersion,
            duration: updateData.duration,
            success: updateData.success,
            errorCode: updateData.errorCode,
            timestamp: new Date(),
            location: updateData.location,
            connectionType: updateData.connectionType,
            dataUsage: updateData.dataUsage
        };
        
        await this.database.analytics.insertOne(analytics);
        
        // Atualizar métricas em tempo real
        await this.updateMetrics(analytics);
    }

    async getDashboardMetrics(userId) {
        const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        
        const metrics = await this.database.analytics.aggregate([
            {
                $match: {
                    userId,
                    timestamp: { $gte: thirtyDaysAgo }
                }
            },
            {
                $group: {
                    _id: null,
                    totalUpdates: { $sum: 1 },
                    successRate: { 
                        $avg: { $cond: ['$success', 1, 0] }
                    },
                    totalDataUsage: { $sum: '$dataUsage' },
                    averageDuration: { $avg: '$duration' }
                }
            }
        ]).toArray();
        
        return metrics[0] || {
            totalUpdates: 0,
            successRate: 0,
            totalDataUsage: 0,
            averageDuration: 0
        };
    }
}