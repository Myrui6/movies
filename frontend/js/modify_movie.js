const { createApp } = Vue;

createApp({
    data() {
        return {
            movieData: null,
            pictureFile: null,
            message: ''
        }
    },
    mounted() {
        this.loadMovieData();
    },
    methods: {
        async loadMovieData() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('id');

                if (!movieId) {
                    this.message = 'Movie ID not provided';
                    return;
                }

                const response = await fetch(`/api/movies/${movieId}`);
                const result = await response.json();

                if (result.success) {
                    this.movieData = result.data;
                } else {
                    this.message = result.message;
                }
            } catch (error) {
                console.error('Load movie data error:', error);
                this.message = 'Failed to load movie data';
            }
        },

        handleFileUpload(event) {
            this.pictureFile = event.target.files[0];
        },

        async submitForm() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('id');

                if (!movieId || !this.movieData) {
                    this.message = 'Movie ID or data missing';
                    return;
                }

                const formData = new FormData();
                formData.append('name', this.movieData.name);
                formData.append('type', this.movieData.type);
                formData.append('region', this.movieData.region);
                formData.append('time', this.movieData.time);
                formData.append('brief', this.movieData.brief);

                if (this.pictureFile) {
                    formData.append('picture', this.pictureFile);
                }

                const response = await fetch(`/api/movies/${movieId}`, {
                    method: 'PUT',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert('Movie updated successfully!');
                    window.location.href = '/home';
                } else {
                    this.message = 'Update failed: ' + result.message;
                }
            } catch (error) {
                console.error('Update movie error:', error);
                this.message = 'Network error, please try again';
            }
        }
    }
}).mount('#app');