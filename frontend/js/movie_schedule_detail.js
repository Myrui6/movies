const { createApp } = Vue;

createApp({
    data() {
        return {
            movie: {
                name: '',
                picture: '',
                type: '',
                region: '',
                time: '',
                brief: ''
            },
            schedules: []
        }
    },
    mounted() {
        this.loadMovieDetail();
        this.loadSchedules();
    },
    methods: {
        async loadMovieDetail() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('id');

                if (!movieId) {
                    alert('Invalid movie ID');
                    window.location.href = '/home';
                    return;
                }

                const response = await fetch(`/api/movies/${movieId}`);
                const result = await response.json();

                if (result.success) {
                    this.movie = result.data;
                } else {
                    alert('Failed to load movie details: ' + result.message);
                    window.location.href = '/home';
                }
            } catch (error) {
                alert('Network error, please try again');
                window.location.href = '/home';
            }
        },

        async loadSchedules() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('id');

                if (!movieId) return;

                const response = await fetch(`/api/schedules/movie/${movieId}`);
                const result = await response.json();

                if (result.success) {
                    this.schedules = result.data;
                } else {
                    console.error('Failed to load schedules:', result.message);
                    this.schedules = [];
                }
            } catch (error) {
                console.error('Network error:', error);
                this.schedules = [];
            }
        },

        addSchedule() {
            const urlParams = new URLSearchParams(window.location.search);
            const movieId = urlParams.get('id');

            if (movieId && this.movie.name) {
                window.location.href = `/add-schedule?movie_id=${movieId}&movie_name=${encodeURIComponent(this.movie.name)}`;
            } else {
                alert('Cannot get movie information');
            }
        },

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString();
        },

        async deleteSchedule(scheduleId, movieName) {
            if (confirm(`Are you sure to delete this schedule for "${movieName}"?\n\nNote: This will also delete all seat information for this schedule!`)) {
                try {
                    console.log('Deleting schedule ID:', scheduleId);

                    const response = await fetch(`/api/schedules/${scheduleId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message);
                        this.loadSchedules();
                    } else {
                        alert('Delete failed: ' + result.message);
                    }
                } catch (error) {
                    console.error('Schedule deletion error:', error);
                    alert('Network error, please try again');
                }
            }
        }
    }
}).mount('#app');