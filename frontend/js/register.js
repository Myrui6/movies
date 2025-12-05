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

            if (!this.username || !this.password) {
                this.message = 'Please enter username and password';
                return;
            }

            if (this.password !== this.confirmPassword) {
                this.message = 'Passwords do not match';
                return;
            }

            if (this.password.length < 6) {
                this.message = 'Password must be at least 6 characters';
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
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                } else {
                    this.message = result.message;
                }
            } catch (error) {
                this.message = 'Network error, please try again';
            }
        },

        goToLogin() {
            window.location.href = '/';
        }
    }
}).mount('#app');