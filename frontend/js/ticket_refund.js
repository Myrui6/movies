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
                // 后续实现退票提交功能
                alert('退票申请提交成功！\n订单编号：' + this.orderId + '\n原因：' + this.reason);
                // 暂时跳转回订单页面
                window.location.href = '/my-order';
            } catch (error) {
                alert('提交失败，请重试');
            }
        }
    }
}).mount('#app');