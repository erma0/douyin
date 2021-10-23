<?php
header('Content-type: application/json');

$_url = $_GET['url'];

function get_url($_url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $_url);
    // 不需要页面内容
    curl_setopt($ch, CURLOPT_HEADER, TRUE);  
    curl_setopt($ch, CURLOPT_NOBODY, TRUE);
    // 不直接输出
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    // 设置UA
    curl_setopt($ch,CURLOPT_USERAGENT,'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Mobile Safari/537.36'); 
    // 跟随重定向
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    // 发送
    $response=curl_exec($ch);
    // 获取最后连接的地址
    $info = curl_getinfo($ch,CURLINFO_EFFECTIVE_URL);
    //关闭句柄
    curl_close($ch);
    //echo $info;
    return $info; 
}


if(strpos($_url,'com') !== false){
    $_res = file_get_contents($_url);
    preg_match('/playAddr: \"(.*?)\"/', $_res, $_m);
    preg_match('/name nowrap\">(.*?)</', $_res, $_user);
    preg_match('/desc\">(.*?)</', $_res, $_desc);
    $_v1 = str_replace("line=0","line=1",str_replace("playwm","play",$_m[1]));
    // get_url函数无效，因为curl设置UA无法使用，原因未知，导致无法获取视频真实地址，但手机端仍旧可解析
    $_v = get_url($_v1);
    if($_v==''){
    $_c = 0701.1;
    $_s = 'error';
    }else{
        $_c = 0;
        $_s = 'success';
    }
}else{
        $_c = 0701.2;
        $_s = 'url does not match';
}
echo json_encode(array("code" => $_c,"message" => $_GET['url'],"user_name" => $_user[1],"description" => $_desc[1], "errMsg" => $_s,"videoUrl" => $_v,"tmp" => time()), JSON_UNESCAPED_SLASHES);
?>