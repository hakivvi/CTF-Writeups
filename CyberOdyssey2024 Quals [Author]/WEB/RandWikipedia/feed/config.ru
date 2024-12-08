require 'rack'
require 'securerandom'
require 'digest'

class FeedApp
  def call(env)
    request = Rack::Request.new(env)

    headers = {'content-type' => 'text/html'}
    iframe_html = get_html_doc(request.params['style'] || '')
    headers.merge!({'connection': 'keep-alive', 'content-length' => iframe_html.size.to_s})
    
    if request.path == "/fortify/feed" && (request.cookies['client_id'].nil? || request.cookies['client_id'].empty?)
      id = Digest::MD5.hexdigest(SecureRandom.hex(30))
      headers.merge!({'X-Client-Id': id, 'Set-Cookie' => "client_id=#{id}; Path=/fortify/feed"})
    elsif request.path == "/fortify/feed" && request.cookies['client_id']
      headers.merge!({'X-Client-Id': request.cookies['client_id']})
    end

    [200, headers, [iframe_html]]
  end

  private
  def get_html_doc(style)
    %(<html><head><style>body, html { margin: 0; padding: 0; height: 100%; }
      iframe { width: 100%; height: 100%; border: none; }
      #{style}</style></head><body><iframe src="https://en.wikipedia.org/wiki/Special:Random"></iframe></body></html>)
  end
end

run FeedApp.new
