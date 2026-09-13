<?php
/** Em LP, omite do sitemap as paginas antigas atendidas no dominio principal. */
function cm_static_slugs() {
    return array('bce', 'coe', 'drb', 'mce', 'mpg', 'gdp', 'ecm-26', 'ecm-26-v1');
}

add_filter('wp_sitemaps_posts_query_args', function ($args, $post_type) {
    if ($post_type !== 'page') {
        return $args;
    }
    $ids = get_posts(array(
        'post_type' => 'page',
        'post_status' => 'publish',
        'post_name__in' => cm_static_slugs(),
        'fields' => 'ids',
        'numberposts' => -1,
    ));
    $args['post__not_in'] = array_unique(array_merge($args['post__not_in'] ?? array(), $ids));
    return $args;
}, 10, 2);
