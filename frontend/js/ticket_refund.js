const { createApp } = Vue;

createApp({
    data() {
        return {
            username: '',
            orderId: '',
            reason: ''
        }
    },
    mounted() {
        this.getCurrentUser();
        this.getOrderIdFromUrl();
    },
    methods: {
        async getCurrentUser() {
            try {
                const response = await fetch('/api/current-user');
                const result = await response.json();

                if (result.success) {
                    this.username = result.data.username;
                } else {
                    console.error('Failed to get user info:', result.message);
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Network error:', error);
                window.location.href = '/';
            }
        },

        getOrderIdFromUrl() {
            const urlParams = new URLSearchParams(window.location.search);
            const orderId = urlParams.get('order_id');
            if (orderId) {
                this.orderId = orderId;
            } else {
                alert('Invalid order ID');
                window.location.href = '/my-order';
            }
        },

        autoResizeTextarea(event) {
            const textarea = event.target;
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        },

        async submitRefund() {
            if (!this.reason.trim()) {
                alert('Please enter refund reason');
                return;
            }

            try {
                const response = await fetch(`/api/orders/${this.orderId}/refund`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        reason: this.reason
                    })
                });

                const result = await response.json();

                if (result.success) {
                    alert('Refund application submitted successfully!');
                    window.location.href = '/my-order';
                } else {
                    alert('Submission failed: ' + result.message);
                }
            } catch (error) {
                console.error('Submission error:', error);
                alert('Network error, please try again');
            }
        }
    }
}).mount('#app');