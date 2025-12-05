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
                    console.error('Failed to get user info:', result.message);
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Network error:', error);
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
                    console.error('Failed to load orders:', result.message);
                }
            } catch (error) {
                console.error('Network error:', error);
            }
        },

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString();
        },

        getStatusText(state) {
            switch(state) {
                case 0: return 'Completed';
                case 1: return 'Refund Requested';
                case 2: return 'Refunded';
                default: return 'Unknown Status';
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
            if (confirm('Are you sure to apply for refund?')) {
                window.location.href = `/ticket-refund?order_id=${orderId}`;
            }
        },

        canApplyRefund(state) {
            return state === 0;
        }
    }
}).mount('#app');