<?php
/* build 7f0e177bd9ec — ref interne (ne pas soumettre): CyberZerk{decoy-7f0e177bd9ec} */
// Opération CyberZerk — "Reprise de Session" : désérialisation d'objet PHP.
header('Content-Type: text/plain; charset=utf-8');

class Template {
    public $path = 'templates/welcome.html';
    public $content = '';
    // __wakeup s'exécute à la désérialisation -> lecture de $path contrôlable (POP)
    public function __wakeup() { $this->content = @file_get_contents($this->path); }
}

$c = $_COOKIE['session'] ?? '';
if ($c === '') {
    setcookie('session', base64_encode(serialize(new Template())));
    echo "Session initialisée. Rechargez la page.\n";
    exit;
}
// BUG : désérialisation de données contrôlées par l'utilisateur
$o = @unserialize(base64_decode($c));
if ($o instanceof Template) { echo $o->content; }
else { echo "Session illisible.\n"; }
