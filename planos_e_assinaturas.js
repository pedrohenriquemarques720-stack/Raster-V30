// Estrutura de Planos
const subscriptionPlans = {
    free: {
        name: "Básico",
        price: 0,
        features: [
            "Atualizações críticas de segurança",
            "1 dispositivo",
            "Suporte comunitário",
            "Logs básicos"
        ],
        limits: {
            updatesPerMonth: 1,
            devicesAllowed: 1,
            supportLevel: 'community',
            diagnosticPackages: ['basic']
        }
    },
    professional: {
        name: "Profissional",
        price: 49.90,
        period: "monthly",
        features: [
            "Todas as atualizações de firmware",
            "Até 3 dispositivos",
            "Suporte prioritário 12/7",
            "Backup automático",
            "Diagnósticos avançados",
            "Relatórios detalhados"
        ],
        limits: {
            updatesPerMonth: 'unlimited',
            devicesAllowed: 3,
            supportLevel: 'priority',
            diagnosticPackages: ['basic', 'advanced', 'commercial']
        }
    },
    enterprise: {
        name: "Enterprise",
        price: 199.90,
        period: "monthly",
        features: [
            "Tudo do plano Profissional",
            "Dispositivos ilimitados",
            "Suporte 24/7 com SLA",
            "API dedicada",
            "Treinamento presencial",
            "Personalização de firmware",
            "Auditoria de segurança"
        ],
        limits: {
            updatesPerMonth: 'unlimited',
            devicesAllowed: 'unlimited',
            supportLevel: 'dedicated',
            diagnosticPackages: ['all']
        }
    }
};