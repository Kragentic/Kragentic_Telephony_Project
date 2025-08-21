defmodule KragenticTelephony.RAGTest do
  use ExUnit.Case, async: true

  alias KragenticTelephony.RAG

  describe "RAG Service" do
    test "uploads a document successfully" do
      result = RAG.upload_document("Our refund policy is 30 days.")
      assert result[:status] == "success"
      assert result[:result][:status] == "success"
    end

    test "uploads multiple documents successfully" do
      documents = [
        %{
          "content" => "Our refund policy is 30 days.",
          "metadata" => %{},
          "doc_type" => "text",
          "source" => "test"
        },
        %{
          "content" => "Our return policy allows exchanges within 14 days.",
          "metadata" => %{},
          "doc_type" => "text",
          "source" => "test"
        }
      ]
      result = RAG.upload_documents_batch(documents)
      assert result[:status] == "success"
      assert result[:result][:successful] > 0
    end
  end
end
