<?php
session_start();

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $firstName = trim($_POST['firstName']);
    $lastName = trim($_POST['lastName']);
    $email = trim($_POST['email']);
    $country = trim($_POST['country']);
    $state = trim($_POST['state']);
    $userIp = $_SERVER['REMOTE_ADDR'];
    $currentTime = time();

    if (empty($firstName) || empty($lastName) || empty($email) || empty($country) || empty($state)) {
        echo "All fields are required.";
        exit;
    }

    if (isset($_SESSION['last_submission_time']) && $currentTime - $_SESSION['last_submission_time'] < 3600) {
        echo "You can only submit once per hour.";
        exit;
    }

    try {
        $message = "First Name: $firstName\n\nLast Name: $lastName\n\nCountry: $country\n\nState: $state\n\nEmail: $email";
        sendToTelegram($message);
        $_SESSION['last_submission_time'] = $currentTime;
        echo "Application sent successfully!";
    } catch (Exception $e) {
        echo 'Error: ' . $e->getMessage();
    }
} else {
    echo "Invalid request method.";
}

function sendToTelegram($message) {
    // Telegram Bot API token
    $botToken = "7460363720:AAE_1X_Cwm3sJ9RMJFNha04mbzgJ-m8JBys";
    
    // Your private channel ID (with -100 prefix)
    $channelId = "6736572379";  // Replace with your actual channel ID

    // The message you want to send
    // Telegram API URL
    $url = "https://api.telegram.org/bot$botToken/sendMessage";

    // Data to be sent
    $data = [
        'chat_id' => $channelId,
        'text' => $message
    ];

    // Use cURL to send the request
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);

    // Close cURL session
    curl_close($ch);

    // Check response
    $responseData = json_decode($response, true);
    if (!$responseData || !$responseData['ok']) {
        throw new Exception("Failed to send message: " . ($responseData['description'] ?? 'Unknown error'));
    }
}
?>