const { createApp } = Vue;

createApp({
    data() {
        return {
            formData: {
                name: '',
                type: '',
                region: '',
                time: '',
                brief: ''
            },
            pictureFile: null
        }
    },
    methods: {
        handleFileUpload(event) {
            this.pictureFile = event.target.files[0];
        },

        async submitForm() {
            try {
                const formData = new FormData();
                formData.append('name', this.formData.name);
                formData.append('type', this.formData.type);
                formData.append('region', this.formData.region);
                formData.append('time', this.formData.time);
                formData.append('brief', this.formData.brief);

                if (this.pictureFile) {
                    formData.append('picture', this.pictureFile);
                }

                const response = await fetch('/api/movies', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert('影片添加成功！');
                    window.location.href = '/home';
                } else {
                    alert('添加失败：' + result.message);
                }
            } catch (error) {
                alert('网络错误，请重试');
            }
        }
    }
}).mount('#app');