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
            schedules: [],
            username: 'user'
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
                const movieId = urlParams.get('movie_id');

                if (!movieId) {
                    alert('Invalid movie ID');
                    window.location.href = '/user-buy';
                    return;
                }

                const response = await fetch(`/api/movies/${movieId}`);
                const result = await response.json();

                if (result.success) {
                    this.movie = result.data;
                } else {
                    alert('Failed to load movie details: ' + result.message);
                    window.location.href = '/user-buy';
                }
            } catch (error) {
                alert('Network error, please try again');
                window.location.href = '/user-buy';
            }
        },

        async loadSchedules() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('movie_id');

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

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString();
        },

        chooseSeat(scheduleId) {
            window.location.href = `/choose-seat?schedule_id=${scheduleId}&username=${this.username}`;
        }
    }
}).mount('#app');