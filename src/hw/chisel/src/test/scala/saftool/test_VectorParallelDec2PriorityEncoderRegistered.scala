import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.freespec.AnyFreeSpec
import org.scalatest.flatspec.AnyFlatSpec
import java.nio.file.{Files, Paths, StandardOpenOption}
import java.nio.charset.StandardCharsets

class Workload_VectorParallelDec2PriorityEncoderRegistered_Random(penc: VectorParallelDec2PriorityEncoderRegistered) extends PeekPokeTester(penc) {
  val rand = new scala.util.Random

  reset(2)
  step(3)

  poke(penc.io.enable, true)

  for (i <- 0 to 100) {
    poke(penc.io.input, rand.nextInt())
    step(1)
  }
}

class Test_Sim_VectorParallelDec2PriorityEncoderRegistered extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "VectorParallelDec2PriorityEncoderRegistered"

  val chiselTestDir = sys.env.getOrElse("CHISEL_TEST_DIR", "src/test/scala/saftool") // Default path if the environment variable is not set
  var verilog_dir = "src/verilog/"

  val inputbitsValues = List(1, 2, 4, 8, 16, 32, 64)
  val vectorLengthValues = List(1, 2, 4)

  val combinations = for {
    inputbits <- inputbitsValues
    vectorLength <- vectorLengthValues
    if inputbits >= vectorLength
  } yield (inputbits, vectorLength)

  def createTest(inputbits: Int, vectorLength: Int): Unit = {
    val testName = s"test_VectorParallelDec2PriorityEncoderRegistered_inputbits${inputbits}_vectorLength${vectorLength}.scala"
    val testFilePath = Paths.get(chiselTestDir, testName)

    if (!Files.exists(testFilePath)) {
      Files.createFile(testFilePath)
    }

    it should s"inputbits${inputbits}_vectorLength${vectorLength}" in {
      test(new VectorParallelDec2PriorityEncoderRegistered(vectorLength, inputbits))
        .withAnnotations(Seq(WriteVcdAnnotation))
        .runPeekPoke(new Workload_VectorParallelDec2PriorityEncoderRegistered_Random(_))
    }
    emitVerilog(inputbits, vectorLength)
  }

  def emitVerilog(inputbits: Int, vectorLength: Int): Unit = {
    val filename = s"VectorParallelDec2PriorityEncoderRegistered_inputbits${inputbits}_vectorLength${vectorLength}.v"
    val verilogString = chisel3.getVerilogString(new VectorParallelDec2PriorityEncoderRegistered(vectorLength, inputbits))
    Files.write(Paths.get(verilog_dir + filename), verilogString.getBytes(StandardCharsets.UTF_8))
  }

  combinations.foreach { case (inputbits, vectorLength) =>
    createTest(inputbits, vectorLength)
  }
}