import saftool._
import chisel3._
import chisel3.util._
import chiseltest._
import chiseltest.iotesters._
import treadle.WriteVcdAnnotation
import org.scalatest.matchers.should.Matchers
import org.scalatest.flatspec.AnyFlatSpec

class TestVectorFillGatherReadMemory(dut: VectorFillGatherReadMemory) extends PeekPokeTester(dut) {
  val rand = new scala.util.Random
  val enableAssertions = false // Flag to enable/disable assertions

  def createErrorMessage(expected: Any, actual: Any, inputs: Map[String, Any]): String = {
    val inputStr = inputs.map { case (key, value) => s"$key: $value" }.mkString(", ")
    s"Expected $expected, found $actual. Inputs: $inputStr"
  }

  reset(2)
  step(3)

  for (i <- 0 until 100) {
    val enableValue = rand.nextBoolean()
    val writeEnableValue = rand.nextBoolean()
    val pingpongSelectValue = rand.nextBoolean()

    // Ensure these interfaces exist in VectorFillGatherReadMemory
    val writeDataValues = Seq.fill(dut.numRegisters)(rand.nextInt(math.pow(2, dut.bitWidth).toInt))
    val readAddresses = Seq.fill(dut.readPorts)(rand.nextInt(dut.numRegisters))
    val readEnableValues = Seq.fill(dut.readPorts)(rand.nextBoolean())

    // Ensure these signals exist and are correctly named in VectorFillGatherReadMemory
    poke(dut.io.enable, if (enableValue) 1 else 0)
    poke(dut.io.writeEnable, if (writeEnableValue) 1 else 0)
    poke(dut.io.pingpongSelect, if (pingpongSelectValue) 1 else 0)

    // Write data to the module
    writeDataValues.zipWithIndex.foreach { case (value, index) =>
      poke(dut.io.writeData(index), value)
    }

    // Set read addresses and enables
    readAddresses.zipWithIndex.foreach { case (address, index) =>
      poke(dut.io.readAddresses(index), address)
    }
    readEnableValues.zipWithIndex.foreach { case (enable, index) =>
      poke(dut.io.readEnable(index), if (enable) 1 else 0)
    }

    step(1)

    if (enableAssertions) {
      // Implement your assertions here
    }
  }
}

class TestSimVectorFillGatherReadMemory extends AnyFlatSpec with ChiselScalatestTester {
  behavior of "VectorFillGatherReadMemory"
  it should "handle vector writes with random multi-port reads" in {
    test(new VectorFillGatherReadMemory(bitWidth = 32, numRegisters = 8, readPorts = 4)).withAnnotations(Seq(WriteVcdAnnotation)).runPeekPoke(new TestVectorFillGatherReadMemory(_))
  }
}
