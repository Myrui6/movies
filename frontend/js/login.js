const { createApp } = Vue;

createApp({
    data() {
        return {
            username: '',
            password: '',
            userType: '用户',
            message: ''
        }
    },
    methods: {
        async login() {
            this.message = '';

            if (!this.username || !this.password) {
                this.message = '请输入用户名和密码';
                return;
            }

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password,
                        userType: this.userType
                    })
                });

                const result = await response.json();

                if (result.success) {
                    // 根据用户类型跳转到不同页面
                    window.location.href = result.redirect;
                } else {
                    this.message = result.message;
                }
            } catch (error) {
                this.message = '网络错误';
            }
        },
        
        register() {
            this.message = '注册功能暂未开放';
        }
    }
}).mount('#app');