const { createApp } = Vue;

createApp({
    data() {
        return {
            movies: [],
            username: 'user'
        }
    },
    mounted() {
        this.loadMoviesWithSchedules();
    },
    methods: {
        async loadMoviesWithSchedules() {
            try {
                const response = await fetch('/api/movies/with-schedules');
                const result = await response.json();

                if (result.success) {
                    this.movies = result.data;
                } else {
                    console.error('加载影片失败:', result.message);
                }
            } catch (error) {
                console.error('网络错误:', error);
            }
        },

        buyTicket(movieId) {
            window.location.href = `/choose-schedule?movie_id=${movieId}&username=${this.username}`;
        },

        goToMyOrder() {
            window.location.href = `/my-order?username=${this.username}`;
        }
    }
}).mount('#app');