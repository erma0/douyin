titles = [
    '# 标题',
    '## 标题',
    '### 标题',
    '#### 标题',
    '#### 标题',
    '## 标题',
    '### 标题',
    '#### 标题',
    '# 标题',
    '## 标题',
]
nums = []
num = [0, 0, 0, 0]
for j, title in enumerate(titles):
    index = title.index(' ')
    text = title[index + 1:]
    now = len(title[:index])
    nums.append(now)
    if j > 0 and now > nums[j - 1]:
        num[now - 1] = 0
    num[now - 1] += 1
    sn = []
    for i in range(now):
        sn.append(str(num[i]))
    print('{} {}'.format('.'.join(sn), text))
