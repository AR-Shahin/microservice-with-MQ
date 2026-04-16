<?php

use Illuminate\Support\Facades\Artisan;

Artisan::command('inspire', function () {
    \$this->comment('Keep it simple.');
})->purpose('Display an inspiring quote');
