<?php

if (!isset($_REQUEST)) {
  return;
}

//Строка для подтверждения адреса сервера из настроек Callback API
$confirmation_token = 'd3ac7af4';

//Ключ доступа сообщества
$token = '01ad426dff6f989b27d6db76274d220f80e11ecbdb74def010e0bddedec3c5a00e5f21434b5678b6c03df';

//Получаем и декодируем уведомление
$data = json_decode(file_get_contents('php://input'));

//Проверяем, что находится в поле "type"
switch ($data->type) {
  //Если это уведомление для подтверждения адреса сервера...
  case 'confirmation':
    //...отправляем строку для подтверждения адреса
    echo $confirmation_token;
    break;

//Если это уведомление о новом сообщении...
  case 'message_new':
    //...получаем id его автора
    $user_id = $data->object->user_id;
    $user_body = $data->object->body;
    //затем с помощью users.get получаем данные об авторе
    $user_info = json_decode(file_get_contents("https://api.vk.com/method/users.get?user_ids={$user_id}&v=5.0"));

//и извлекаем из ответа его имя
    $user_name = $user_info->response[0]->first_name;

if ($user_body=="fff") {
//С помощью messages.send и токена сообщества отправляем ответное сообщение
    $request_params = array(
      'message' => "Привет, {$user_name}!",
      'user_id' => $user_id,
      'access_token' => $token,
      'v' => '5.0'
    );
$get_params = http_build_query($request_params);
file_get_contents('https://api.vk.com/method/messages.send?'. $get_params);
//Возвращаем "ok" серверу Callback API
    echo('ok');
break;}

else {
//С помощью messages.send и токена сообщества отправляем ответное сообщение
    $request_params = array(
      'message' => "Hello, {$user_name}!",
      'user_id' => $user_id,
      'access_token' => $token,
      'v' => '5.0'
    );
$get_params = http_build_query($request_params);
file_get_contents('https://api.vk.com/method/messages.send?'. $get_params);
//Возвращаем "ok" серверу Callback API
    echo('ok');
break;
}
}
?>