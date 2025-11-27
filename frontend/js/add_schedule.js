const { createApp } = Vue;

createApp({
    data() {
        return {
            formData: {
                movie_name: '',
                start_time: '',
                hall: '',
                seat_rows: '',
                seat_columns: '',
                price: '',
                movie_id: ''
            }
        }
    },
    mounted() {
        this.loadMovieInfo();
    },
    methods: {
        loadMovieInfo() {
            // 从URL参数获取电影ID和名称
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

        async submitForm() {
            try {
                // 验证表单 - 移除movie_name的验证，因为它已经自动填充
                if (!this.formData.start_time || !this.formData.hall ||
                    !this.formData.seat_rows || !this.formData.seat_columns || !this.formData.price) {
                    alert('请填写所有必填字段');
                    return;
                }

                const response = await fetch('/api/schedules', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.formData)
                });

                const result = await response.json();

                if (result.success) {
                    alert('场次添加成功！');
                    // 返回到影片详情页面
                    window.location.href = `/movie-schedule-detail?id=${this.formData.movie_id}`;
                } else {
                    alert('添加失败：' + result.message);
                }
            } catch (error) {
                alert('网络错误，请重试');
            }
        }
    }
}).mount('#app');