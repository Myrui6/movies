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
                    console.error('Failed to get user info:', result.message);
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Network error:', error);
                window.location.href = '/';
            }
        },

        async loadMoviesWithSchedules() {
            try {
                const response = await fetch('/api/movies/with-schedules');
                const result = await response.json();

                if (result.success) {
                    if (this.searchKeyword) {
                        const keyword = this.searchKeyword.toLowerCase();
                        this.movies = result.data.filter(movie =>
                            movie.name && movie.name.toLowerCase().includes(keyword)
                        );
                    } else {
                        this.movies = result.data;
                    }
                } else {
                    console.error('Failed to load movies:', result.message);
                    this.movies = [];
                }
            } catch (error) {
                console.error('Network error:', error);
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