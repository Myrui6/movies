const { createApp } = Vue;

createApp({
    data() {
        return {
            formData: {
                movie_name: '',
                start_time: '',
                hall_id: '',
                price: '',
                movie_id: ''
            },
            halls: [],
            message: ''
        }
    },
    mounted() {
        this.loadMovieInfo();
        this.loadHalls();
    },
    methods: {
        loadMovieInfo() {
            const urlParams = new URLSearchParams(window.location.search);
            const movieId = urlParams.get('movie_id');
            const movieName = urlParams.get('movie_name');

            if (movieId && movieName) {
                this.formData.movie_id = movieId;
                this.formData.movie_name = decodeURIComponent(movieName);
            } else {
                alert('Invalid movie information');
                window.history.back();
            }
        },

        async loadHalls() {
            this.message = 'Loading halls...';
            try {
                const response = await fetch('/api/halls');
                const result = await response.json();

                if (result.success) {
                    this.halls = result.data;
                    this.message = '';
                } else {
                    console.error('Failed to load halls:', result.message);
                    this.message = 'Failed to load hall list: ' + result.message;
                }
            } catch (error) {
                console.error('Network error:', error);
                this.message = 'Network error, cannot load hall list.';
            }
        },

        async submitForm() {
            this.message = '';

            try {
                if (!this.formData.start_time || !this.formData.hall_id || !this.formData.price) {
                    this.message = 'Please fill all required fields';
                    return;
                }

                const response = await fetch('/api/schedules', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        movie_id: this.formData.movie_id,
                        hall_id: this.formData.hall_id,
                        start_time: this.formData.start_time,
                        price: this.formData.price
                    })
                });

                const result = await response.json();

                if (result.success) {
                    alert('Schedule added successfully!' + result.message);
                    window.location.href = `/movie-schedule-detail?id=${this.formData.movie_id}`;
                } else {
                    this.message = 'Failed to add: ' + result.message;
                    alert('Failed to add: ' + result.message);
                }
            } catch (error) {
                this.message = 'Network error, please try again';
                alert('Network error, please try again');
            }
        }
    }
}).mount('#app');