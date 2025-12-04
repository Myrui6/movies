const { createApp } = Vue;

createApp({
    data() {
        return {
            formData: {
                movie_name: '',
                start_time: '',
                hall_id: '', // 核心修改：改为发送 hall_id
                price: '',
                movie_id: ''
            },
            halls: [], // 新增：用于存储影厅列表
            message: ''
        }
    },
    mounted() {
        this.loadMovieInfo();
        this.loadHalls(); // 新增：加载影厅列表
    },
    methods: {
        loadMovieInfo() {
            // ... (保持不变) ...
            const urlParams = new URLSearchParams(window.location.search);
            const movieId = urlParams.get('movie_id');
            const movieName = urlParams.get('movie_name');

            if (movieId && movieName) {
                this.formData.movie_id = movieId;
                this.formData.movie_name = decodeURIComponent(movieName);
            } else {
                alert('无效的电影信息');
                window.history.back();
            }
        },

        // 新增方法：加载影厅列表
        async loadHalls() {
            this.message = '正在加载影厅...';
            try {
                const response = await fetch('/api/halls');
                const result = await response.json();

                if (result.success) {
                    this.halls = result.data;
                    this.message = '';
                } else {
                    console.error('加载影厅失败:', result.message);
                    this.message = '加载影厅列表失败：' + result.message;
                }
            } catch (error) {
                console.error('网络错误:', error);
                this.message = '网络错误，无法加载影厅列表。';
            }
        },

        async submitForm() {
            this.message = '';

            try {
                // 验证表单 - 核心修改：只检查 hall_id 和 price
                if (!this.formData.start_time || !this.formData.hall_id || !this.formData.price) {
                    this.message = '请填写所有必填字段';
                    return;
                }

                const response = await fetch('/api/schedules', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    // 核心修改：只发送 movie_id, hall_id, start_time, price
                    body: JSON.stringify({
                        movie_id: this.formData.movie_id,
                        hall_id: this.formData.hall_id,
                        start_time: this.formData.start_time,
                        price: this.formData.price
                    })
                });

                const result = await response.json();

                if (result.success) {
                    alert('场次添加成功！' + result.message);
                    window.location.href = `/movie-schedule-detail?id=${this.formData.movie_id}`;
                } else {
                    this.message = '添加失败：' + result.message;
                    alert('添加失败：' + result.message);
                }
            } catch (error) {
                this.message = '网络错误，请重试';
                alert('网络错误，请重试');
            }
        }
    }
}).mount('#app');