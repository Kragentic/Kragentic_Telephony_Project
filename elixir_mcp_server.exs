IO.puts("Elixir MCP server started")

defmodule MCPServer do
  def loop do
    case IO.gets("") do
      :eof -> 
        IO.puts("Connection closed")
        :ok
      {:error, reason} ->
        IO.puts("Stream error: #{inspect(reason)}")
        :ok
      line when is_binary(line) ->
        # Process the input line here
        IO.puts("Received: #{String.trim(line)}")
        loop()
    end
  end
end

MCPServer.loop()