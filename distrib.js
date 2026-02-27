class FirmwareDistributor {
    async getDownloadUrl(deviceId, firmwareVersion, licenseToken) {
        // 1. Validar permissão
        const canDownload = await this.validateDownloadPermission(
            deviceId, 
            firmwareVersion, 
            licenseToken
        );
        
        if (!canDownload) {
            throw new Error('UNAUTHORIZED_DOWNLOAD');
        }
        
        // 2. Gerar URL temporária assinada
        const url = await this.generateSignedUrl(firmwareVersion, {
            expiresIn: 3600, // 1 hora
            maxDownloads: 3,
            deviceId: deviceId
        });
        
        // 3. Registrar tentativa de download
        await this.logDownloadAttempt(deviceId, firmwareVersion);
        
        return {
            url,
            expiresIn: 3600,
            checksum: await this.getFirmwareChecksum(firmwareVersion)
        };
    }

    async generateSignedUrl(firmwareVersion, options) {
        const params = {
            Bucket: 'firmware-distribution',
            Key: `v29/${firmwareVersion}/firmware.bin`,
            Expires: options.expiresIn,
            ResponseContentDisposition: `attachment; filename="rasther_v29_${firmwareVersion}.bin"`
        };
        
        return this.storage.getSignedUrl('getObject', params);
    }
}