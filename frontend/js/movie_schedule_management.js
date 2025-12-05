const { createApp } = Vue;

createApp({
    data() {
        return {
            movies: [],
            searchKeyword: '',
            allMovies: []
        }
    },
    mounted() {
        this.loadMovies();
    },
    methods: {
        async loadMovies() {
            try {
                const url = this.searchKeyword ? `/api/movies?search=${encodeURIComponent(this.searchKeyword)}` : '/api/movies';
                const response = await fetch(url);
                const result = await response.json();

                if (result.success) {
                    this.movies = result.data;
                    if (!this.searchKeyword) {
                        this.allMovies = result.data;
                    }
                } else {
                    console.error('Failed to load movies:', result.message);
                }
            } catch (error) {
                console.error('Network error:', error);
            }
        },

        async searchMovies() {
            await this.loadMovies();
        },

        scheduleMovie(movieId) {
            window.location.href = `/movie-schedule-detail?id=${movieId}`;
        },

        async removeMovie(movieId, movieName) {
            if (confirm(`Are you sure to remove movie "${movieName}"?\n\nNote: This will also delete all schedule information for this movie!`)) {
                try {
                    const response = await fetch(`/api/movies/${movieId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message);
                        this.loadMovies();
                    } else {
                        alert('Remove failed: ' + result.message);
                    }
                } catch (error) {
                    alert('Network error, please try again');
                }
            }
        }
    }
}).mount('#app');