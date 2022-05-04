new Vue({
    el: '#app',
    data: {},
    methods: {
        uploadSuccess1(response) {
            this.$notify({
                title: '返回数据',
                message: '检测完成',
                type: 'success'
            });
            document.getElementById("result1").innerText = JSON.stringify(response);
        },
        uploadSuccess2(response) {
            this.$notify({
                title: '返回数据',
                message: '检测完成',
                type: 'success'
            });
            document.getElementById("result2").innerText = JSON.stringify(response);
        },
        uploadFail() {
            this.$notify.error({
                title: '错误',
                message: '上传失败'
            });
        },
    }
})