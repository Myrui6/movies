const { createApp } = Vue;

createApp({
    data() {
        return {
            username: '',
            orders: []
        }
    },
    mounted() {
        this.getCurrentUser();
    },
    methods: {
        async getCurrentUser() {
            try {
                const response = await fetch('/api/current-user');
                const result = await response.json();

                if (result.success) {
                    this.username = result.data.username;
                    this.loadOrders();
                } else {
                    console.error('获取用户信息失败:', result.message);
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('网络错误:', error);
                window.location.href = '/';
            }
        },

        async loadOrders() {
            try {
                const response = await fetch('/api/orders');
                const result = await response.json();

                if (result.success) {
                    this.orders = result.data;
                } else {
                    console.error('加载订单失败:', result.message);
                }
            } catch (error) {
                console.error('网络错误:', error);
            }
        },

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString('zh-CN');
        },

        getStatusText(state) {
            switch(state) {
                case 0: return '已完成';
                case 1: return '申请退票中';
                case 2: return '已退票';
                default: return '未知状态';
            }
        },

        getStatusClass(state) {
            switch(state) {
                case 0: return 'status-completed';
                case 1: return 'status-refunding';
                case 2: return 'status-refunded';
                default: return '';
            }
        },

        applyRefund(orderId) {
            if (confirm('确定要申请退票吗？')) {
                alert('申请退票功能开发中...');
            }
        }
    }
}).mount('#app');