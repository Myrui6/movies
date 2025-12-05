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
                this.message = 'Please enter username and password';
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
                    window.location.href = result.redirect;
                } else {
                    this.message = result.message;
                }
            } catch (error) {
                this.message = 'Network error';
            }
        },

        register() {
            window.location.href = '/register';
        }
    }
}).mount('#app');