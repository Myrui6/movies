const { createApp } = Vue;

createApp({
    data() {
        return {
            movies: [],
            username: '',
            searchKeyword: ''
        }
    },
    mounted() {
        this.getCurrentUser();
        this.loadMoviesWithSchedules();
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

        async loadMoviesWithSchedules() {
            try {
                const response = await fetch('/api/movies/with-schedules');
                const result = await response.json();

                if (result.success) {
                    // 如果有搜索关键词，过滤结果
                    if (this.searchKeyword) {
                        const keyword = this.searchKeyword.toLowerCase();
                        this.movies = result.data.filter(movie =>
                            movie.name && movie.name.toLowerCase().includes(keyword)
                        );
                    } else {
                        this.movies = result.data;
                    }
                } else {
                    console.error('加载影片失败:', result.message);
                    this.movies = [];
                }
            } catch (error) {
                console.error('网络错误:', error);
                this.movies = [];
            }
        },

        async searchMovies() {
            await this.loadMoviesWithSchedules();
        },

        buyTicket(movieId) {
            window.location.href = `/choose-schedule?movie_id=${movieId}`;
        },

        goToMyOrder() {
            window.location.href = `/my-order`;
        }
    }
}).mount('#app');