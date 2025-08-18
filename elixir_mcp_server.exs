IO.puts("READY")

defmodule MCPServer do
  def loop do
    case IO.gets("") do
      :eof -> :ok
      {:error, reason} -> IO.puts("Stream error: #{inspect(reason)}")
      line when is_binary(line) ->
        IO.puts("Received: #{String.trim(line)}")
        loop()
    end
  end
end

MCPServer.loop()