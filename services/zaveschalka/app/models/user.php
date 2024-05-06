<?php
class User {
    public function __construct(array $attributes) {
        foreach ($attributes as $name => $value) {
            $this->{$name} = $value;
        }
        $this->save();
    }

    public function save() {
        file_put_contents('./users/'.md5($this->login.getenv('SECRET')).'.txt', serialize($this));
    }
}