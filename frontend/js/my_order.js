const { createApp } = Vue;

createApp({
    data() {
        return {
            username: '',
            orders: []
        }
    },
    mounted() {
        this.getUsername();
        this.loadOrders();
    },
    methods: {
        getUsername() {
            const urlParams = new URLSearchParams(window.location.search);
            const username = urlParams.get('username');
            this.username = username || 'user';
        },

        async loadOrders() {
            try {
                const response = await fetch(`/api/orders?username=${this.username}`);
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
                // 后续实现退票功能
                alert('申请退票功能开发中...');
            }
        }
    }
}).mount('#app');