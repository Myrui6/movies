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
                    console.error('获取用户信息失败:', result.message);
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('网络错误:', error);
                window.location.href = '/';
            }
        },

        getOrderIdFromUrl() {
            const urlParams = new URLSearchParams(window.location.search);
            const orderId = urlParams.get('order_id');
            if (orderId) {
                this.orderId = orderId;
            } else {
                alert('无效的订单ID');
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
                alert('请输入退票原因');
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
                    alert('退票申请提交成功！');
                    window.location.href = '/my-order';
                } else {
                    alert('提交失败：' + result.message);
                }
            } catch (error) {
                console.error('提交错误:', error);
                alert('网络错误，请重试');
            }
        }
    }
}).mount('#app');