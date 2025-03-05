<?php
/**
 * Sample CakePHP 2.10 Controller file with intentional issues for analyzer testing
 */
App::uses('Controller', 'Controller');

class UserController extends AppController {
    public $components = array('Session', 'Auth');

    function beforeFilter() {
        // Deprecated pattern - not calling parent
        $this->Auth->allow('login', 'register');
    }

    public function login() {
        if ($this->request->is('post')) {
            // Deprecated method usage
            if ($this->Auth->login()) {
                $this->Session->setFlash('Logged in successfully');
                $this->redirect($this->Auth->redirectUrl());
            } else {
                $this->Session->setFlash('Invalid username or password');
            }
        }
    }

    public function User_details() {
        // Incorrect method naming (should be camelCase)
        $id = $this->request->params['id'];
        // SQL Injection vulnerability
        $user = $this->User->query("SELECT * FROM users WHERE id = $id");
        $this->set('user', $user);
    }

    public function saveUser() {
        if ($this->request->is('post')) {
            // Mass assignment vulnerability
            if ($this->User->save($this->request->data)) {
                $this->Session->setFlash('User saved');
            }
        }
    }
}
?>
