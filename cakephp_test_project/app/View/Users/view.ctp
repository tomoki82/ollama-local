<?php
/**
 * Sample CakePHP 2.10 View file with intentional issues for analyzer testing
 */
?>
<div class="users view">
    <h2>User Profile</h2>

    <div class="profile-info">
        <h3><?php echo $user['User']['username']; // XSS vulnerability - not using h() ?></h3>

        <!-- Security issue: direct output without escaping -->
        <p>Email: <?= $user['User']['email'] ?></p>

        <!-- Properly escaped output -->
        <p>Name: <?php echo h($user['User']['name']); ?></p>

        <!-- Using HTML helper (safe) -->
        <p>Profile URL: <?php echo $this->Html->link($user['User']['profile_url']); ?></p>
    </div>

    <div class="user-posts">
        <h3>Recent Posts</h3>
        <?php foreach ($userPosts as $post): ?>
            <div class="post">
                <!-- XSS vulnerability -->
                <h4><?= $post['Post']['title'] ?></h4>

                <!-- XSS vulnerability in unescaped content -->
                <div class="content">
                    <?php echo $post['Post']['content']; ?>
                </div>

                <div class="meta">
                    Posted on: <?php echo $this->Time->format('Y-m-d', $post['Post']['created']); ?>
                </div>
            </div>
        <?php endforeach; ?>
    </div>

    <!-- CSRF vulnerability - no SecurityComponent or form token -->
    <form action="/users/update" method="post">
        <input type="text" name="bio" value="<?= $user['User']['bio'] ?>">
        <input type="submit" value="Update Bio">
    </form>
</div>
