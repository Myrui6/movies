const { createApp } = Vue;

createApp({
    data() {
        return {
            username: '',
            password: '',
            confirmPassword: '',
            userType: '用户',
            message: ''
        }
    },
    methods: {
        async register() {
            this.message = '';

            // 验证输入
            if (!this.username || !this.password) {
                this.message = '请输入用户名和密码';
                return;
            }

            if (this.password !== this.confirmPassword) {
                this.message = '两次输入的密码不一致';
                return;
            }

            if (this.password.length < 6) {
                this.message = '密码长度不能少于6位';
                return;
            }

            try {
                const response = await fetch('/api/register', {
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
                    this.message = result.message;
                    // 注册成功后延迟跳转到登录页
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                } else {
                    this.message = result.message;
                }
            } catch (error) {
                this.message = '网络错误，请重试';
            }
        },

        goToLogin() {
            window.location.href = '/';
        }
    }
}).mount('#app');