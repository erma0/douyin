var app = new Vue({
	el: '#app',
	data: {
		loading: false,
		type: 'user',
		target: '',
		types: [{
			value: 'user',
			lable: '作品'
		}, {
			value: 'like',
			lable: '喜欢'
		}, {
			value: 'challenge',
			lable: '话题'
		}, {
			value: 'music',
			lable: '音乐'
		}],
		columns: [
			// 页面大小 620*470
			// {
			// 	prop: 'no',
			// 	label: '序号',
			// 	width: 60
			// }, 
			{
				prop: 'aweme_id',
				label: '作品ID',
				width: 150
			},
			{
				prop: 'desc',
				label: '标题',
				width: 250
			},
			{
				prop: 'play_addr',
				label: '视频地址',
				width: 140
			}
			// ,
			// {
			// 	prop: 'status',
			// 	label: '下载进度',
			// 	width: 100
			// }
		]
	},
	// mounted() {
		// this.setData()
	// },
	methods: {
		start() {
			// this.loading = true
			pywebview.api.init(this.type).then(() => {
				if (this.target.indexOf(':') == 1) {
					console.log(this.target)
					pywebview.api.download_batch(this.target).then(() => {})
				} else {
					pywebview.api.download(this.target).then(() => {})
				}
			})

		},
		pagingScrollTopLeft(val) {
			this.$refs.plTable.pagingScrollTopLeft(val, 0)
		},
		openFile() {
			pywebview.api.openFile().then((text) => {
				this.target = text
				// console.log(text)
				// console.log(this.type)
				// console.log(this.target)
			})
		},
		openSuccess() {
			this.$notify({
				title: '下载完成',
				message: '当前任务已完成',
				type: 'success',
				position: 'bottom-right'
			});
		},
		openError() {
			this.$notify.error({
				title: '错误',
				message: '这是一条错误的提示消息',
				position: 'bottom-right'
			});
		},
		openInfo() {
			this.$notify.info({
				title: '采集完成',
				message: '采集完成，开始下载',
				position: 'bottom-right'
			});
		},
		setData() {
			pywebview.api.videos().then(data => {
				// console.log(data)
				this.$refs.plTable.reloadData(data)
			})
		}
	}
})

window.addEventListener('pywebviewready', function () {
	console.log('pywebview API初始化完成')
})