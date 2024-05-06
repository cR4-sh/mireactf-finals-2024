<?php
class Will {
    public function __construct(array $attributes){
        $this->will_id = md5((string)microtime().getenv('SECRET'));
        foreach ($attributes as $name => $value) {
            $this->{$name} = $value;
        }
        $this->save();
    }

    private function save() {
        file_put_contents('./wills/'.$this->will_id.'.txt', serialize($this));
    }
}