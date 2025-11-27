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
                    console.error('加载电影失败:', result.message);
                }
            } catch (error) {
                console.error('网络错误:', error);
            }
        },

        async searchMovies() {
            await this.loadMovies();
        },

        scheduleMovie(movieId) {
            window.location.href = `/movie-schedule-detail?id=${movieId}`;
        },

        async removeMovie(movieId, movieName) {
            if (confirm(`确定要下架影片《${movieName}》吗？\n\n注意：这将同时删除该影片的所有场次信息！`)) {
                try {
                    const response = await fetch(`/api/movies/${movieId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message); // 显示包含场次删除数量的消息
                        this.loadMovies(); // 重新加载列表
                    } else {
                        alert('下架失败：' + result.message);
                    }
                } catch (error) {
                    alert('网络错误，请重试');
                }
            }
        }
    }
}).mount('#app');