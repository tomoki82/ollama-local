<?php
/**
 * サンプルのユーザー認証クラス
 *
 * このクラスはCakePHP2.10環境でのユーザー認証を処理します
 */
class UserAuthentication {
    private $User;
    private $Session;
    private $Redis;

    /**
     * コンストラクタ
     */
    public function __construct($userModel, $session, $redis) {
        $this->User = $userModel;
        $this->Session = $session;
        $this->Redis = $redis;
    }

    /**
     * ユーザーログイン処理
     *
     * @param string $username ユーザー名
     * @param string $password パスワード
     * @return bool 認証成功時はtrue、失敗時はfalse
     */
    public function login($username, $password) {
        // ユーザー情報を取得
        $user = $this->User->findByUsername($username);

        if (!$user) {
            return false;
        }

        // パスワード検証
        if (md5($password) != $user['User']['password']) {
            return false;
        }

        // セッションにユーザー情報を保存
        $this->Session->write('Auth.User', $user['User']);

        // Redisにセッション情報を保存（有効期限24時間）
        $this->Redis->set('user_session_' . $user['User']['id'], json_encode($user), 86400);

        return true;
    }

    /**
     * ユーザーログアウト処理
     */
    public function logout() {
        $userId = $this->Session->read('Auth.User.id');

        // Redisからセッション情報を削除
        if ($userId) {
            $this->Redis->delete('user_session_' . $userId);
        }

        // セッションからユーザー情報を削除
        $this->Session->delete('Auth.User');

        return true;
    }

    /**
     * 現在のユーザーがログインしているか確認
     */
    public function isLoggedIn() {
        return $this->Session->check('Auth.User.id');
    }
}
