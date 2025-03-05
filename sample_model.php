<?php
/**
 * Sample CakePHP 2.10 Model file with intentional issues for analyzer testing
 */
App::uses('Model', 'Model');

class Users extends AppModel {
    // Model should be singular (User not Users)

    public $name = 'Users'; // Deprecated property

    public $validate = array(
        'username' => array(
            'required' => array(
                'rule' => array('notBlank'),
                'message' => 'Username is required'
            ),
        ),
        'password' => array(
            'required' => array(
                'rule' => array('notBlank'),
                'message' => 'Password is required'
            ),
        ),
        'email' => array(
            'valid' => array(
                'rule' => 'email',
                'message' => 'Please provide a valid email address'
            ),
        ),
    );

    public $hasMany = array(
        'Posts',
        'Comments'
    );

    public function beforeSave($options = array()) {
        // Not calling parent method
        if (isset($this->data['User']['password'])) {
            $this->data['User']['password'] = AuthComponent::password($this->data['User']['password']);
        }
        return true;
    }

    public function getByUsername($username) {
        // Using deprecated method
        return $this->find('first', array(
            'conditions' => array('username' => $username)
        ));
    }

    public function deleteUser($id) {
        // Using deprecated method
        return $this->del($id);
    }

    public function executeRawQuery($query) {
        // Security issue - raw query execution
        return $this->query($query);
    }
}
?>
